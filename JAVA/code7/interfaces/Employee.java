package interfaces;

import java.util.Comparator;

public class Employee implements Comparable<Employee>,Comparator<Employee>
{
   private String name;
   private double salary;

   public Employee(String name, double salary)
   {
      this.name = name;
      this.salary = salary;
   }

   public String getName()
   {
      return name;
   }

   public double getSalary()
   {
      return salary;
      
   }

   public void raiseSalary(double byPercent)
   {
      double raise = salary * byPercent / 100;
      salary += raise;
   }

   /**
    * Compares employees by salary
    * @param other another Employee object
    * @return a negative value if this employee has a lower salary than
    * otherObject, 0 if the salaries are the same, a positive value otherwise
    */
   public int compareTo(Employee other)
   {
      return Double.compare(salary, other.salary);
//      return name.compareTo(other.name);
   }
   @Override
   public int compare(Employee e1,Employee e2)
   {
	   return e1.name.compareTo(e2.name);
	  
   }
   
   public String toString()
   {
      return getClass().getName() + "[name=" + name + ",salary=" + salary  + "]";
   }
}